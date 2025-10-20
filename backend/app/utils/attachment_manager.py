import os
import uuid
import shutil
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import mimetypes
from PIL import Image
import zipfile

from app.core.config import settings
from loguru import logger


class AttachmentManager:
    """附件管理器"""
    
    def __init__(self):
        self.attachments_dir = Path("attachments")
        self.attachments_dir.mkdir(parents=True, exist_ok=True)
        
        # 支持的文件类型
        self.supported_types = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
            'spreadsheet': ['.xls', '.xlsx', '.csv'],
            'archive': ['.zip', '.rar', '.7z']
        }
        
        # 文件大小限制 (bytes)
        self.size_limits = {
            'image': 10 * 1024 * 1024,      # 10MB
            'document': 50 * 1024 * 1024,   # 50MB
            'spreadsheet': 100 * 1024 * 1024, # 100MB
            'archive': 200 * 1024 * 1024     # 200MB
        }
    
    def create_report_attachment_folder(self, report_id: int) -> str:
        """为报告创建附件文件夹"""
        folder_path = self.attachments_dir / f"report_{report_id}"
        folder_path.mkdir(parents=True, exist_ok=True)
        return str(folder_path)
    
    def add_attachment(
        self,
        report_id: int,
        file_path: str,
        original_filename: str,
        attachment_type: str = "document",
        description: str = ""
    ) -> Dict[str, Any]:
        """添加附件到报告"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 验证文件
            file_info = self._validate_file(file_path, original_filename)
            
            # 创建报告附件目录
            report_folder = self.create_report_attachment_folder(report_id)
            
            # 生成新文件名
            file_ext = Path(original_filename).suffix
            new_filename = f"{uuid.uuid4().hex}{file_ext}"
            dest_path = Path(report_folder) / new_filename
            
            # 复制文件
            shutil.copy2(file_path, dest_path)
            
            # 生成缩略图（如果是图片）
            thumbnail_path = None
            if file_info['category'] == 'image':
                thumbnail_path = self._generate_thumbnail(dest_path)
            
            attachment_info = {
                'id': uuid.uuid4().hex,
                'report_id': report_id,
                'original_filename': original_filename,
                'filename': new_filename,
                'file_path': str(dest_path),
                'file_size': file_info['size'],
                'file_type': file_info['mime_type'],
                'category': file_info['category'],
                'thumbnail_path': thumbnail_path,
                'description': description,
                'attachment_type': attachment_type,
                'created_at': datetime.now().isoformat(),
                'checksum': self._calculate_checksum(dest_path)
            }
            
            # 保存附件信息到JSON文件
            self._save_attachment_info(report_id, attachment_info)
            
            logger.info(f"附件添加成功: {original_filename} -> {new_filename}")
            return attachment_info
            
        except Exception as e:
            logger.error(f"添加附件失败: {e}")
            raise
    
    def get_report_attachments(self, report_id: int) -> List[Dict[str, Any]]:
        """获取报告的所有附件"""
        try:
            attachments_file = self.attachments_dir / f"report_{report_id}" / "attachments.json"
            
            if not attachments_file.exists():
                return []
            
            import json
            with open(attachments_file, 'r', encoding='utf-8') as f:
                attachments = json.load(f)
            
            # 验证附件文件是否存在
            valid_attachments = []
            for attachment in attachments:
                if os.path.exists(attachment['file_path']):
                    valid_attachments.append(attachment)
                else:
                    logger.warning(f"附件文件不存在: {attachment['file_path']}")
            
            return valid_attachments
            
        except Exception as e:
            logger.error(f"获取附件列表失败: {e}")
            return []
    
    def delete_attachment(self, report_id: int, attachment_id: str) -> bool:
        """删除附件"""
        try:
            attachments = self.get_report_attachments(report_id)
            
            for i, attachment in enumerate(attachments):
                if attachment['id'] == attachment_id:
                    # 删除文件
                    if os.path.exists(attachment['file_path']):
                        os.remove(attachment['file_path'])
                    
                    # 删除缩略图
                    if attachment.get('thumbnail_path') and os.path.exists(attachment['thumbnail_path']):
                        os.remove(attachment['thumbnail_path'])
                    
                    # 从列表中移除
                    attachments.pop(i)
                    
                    # 更新附件信息文件
                    self._save_all_attachments_info(report_id, attachments)
                    
                    logger.info(f"附件删除成功: {attachment_id}")
                    return True
            
            logger.warning(f"未找到附件: {attachment_id}")
            return False
            
        except Exception as e:
            logger.error(f"删除附件失败: {e}")
            return False
    
    def create_attachment_archive(self, report_id: int) -> Optional[str]:
        """创建附件压缩包"""
        try:
            attachments = self.get_report_attachments(report_id)
            
            if not attachments:
                return None
            
            archive_filename = f"report_{report_id}_attachments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            archive_path = self.attachments_dir / archive_filename
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for attachment in attachments:
                    if os.path.exists(attachment['file_path']):
                        # 使用原始文件名作为压缩包内的文件名
                        zipf.write(attachment['file_path'], attachment['original_filename'])
            
            logger.info(f"附件压缩包创建成功: {archive_path}")
            return str(archive_path)
            
        except Exception as e:
            logger.error(f"创建附件压缩包失败: {e}")
            return None
    
    def cleanup_report_attachments(self, report_id: int) -> bool:
        """清理报告的所有附件"""
        try:
            report_folder = self.attachments_dir / f"report_{report_id}"
            
            if report_folder.exists():
                shutil.rmtree(report_folder)
                logger.info(f"报告附件目录清理成功: report_{report_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"清理报告附件失败: {e}")
            return False
    
    def _validate_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """验证文件"""
        file_size = os.path.getsize(file_path)
        file_ext = Path(filename).suffix.lower()
        
        # 检查文件扩展名
        file_category = None
        for category, extensions in self.supported_types.items():
            if file_ext in extensions:
                file_category = category
                break
        
        if not file_category:
            raise ValueError(f"不支持的文件类型: {file_ext}")
        
        # 检查文件大小
        size_limit = self.size_limits.get(file_category, 50 * 1024 * 1024)
        if file_size > size_limit:
            raise ValueError(f"文件大小超出限制: {file_size} > {size_limit}")
        
        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(filename)
        
        return {
            'size': file_size,
            'category': file_category,
            'mime_type': mime_type or 'application/octet-stream'
        }
    
    def _generate_thumbnail(self, image_path: Path, size: Tuple[int, int] = (200, 200)) -> Optional[str]:
        """生成图片缩略图"""
        try:
            with Image.open(image_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                thumbnail_filename = f"thumb_{image_path.stem}.jpg"
                thumbnail_path = image_path.parent / thumbnail_filename
                
                # 转换为RGB模式（处理RGBA等格式）
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                img.save(thumbnail_path, 'JPEG', quality=85)
                return str(thumbnail_path)
                
        except Exception as e:
            logger.warning(f"生成缩略图失败: {e}")
            return None
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        import hashlib
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _save_attachment_info(self, report_id: int, attachment_info: Dict[str, Any]):
        """保存单个附件信息"""
        attachments = self.get_report_attachments(report_id)
        
        # 检查是否已存在相同ID的附件
        for i, existing in enumerate(attachments):
            if existing['id'] == attachment_info['id']:
                attachments[i] = attachment_info
                break
        else:
            attachments.append(attachment_info)
        
        self._save_all_attachments_info(report_id, attachments)
    
    def _save_all_attachments_info(self, report_id: int, attachments: List[Dict[str, Any]]):
        """保存所有附件信息"""
        import json
        
        report_folder = self.attachments_dir / f"report_{report_id}"
        report_folder.mkdir(parents=True, exist_ok=True)
        
        attachments_file = report_folder / "attachments.json"
        with open(attachments_file, 'w', encoding='utf-8') as f:
            json.dump(attachments, f, ensure_ascii=False, indent=2)
    
    def get_attachment_statistics(self) -> Dict[str, Any]:
        """获取附件统计信息"""
        try:
            total_files = 0
            total_size = 0
            category_stats = {}
            
            for report_folder in self.attachments_dir.glob("report_*"):
                if report_folder.is_dir():
                    attachments = self.get_report_attachments(int(report_folder.name.split('_')[1]))
                    
                    for attachment in attachments:
                        total_files += 1
                        total_size += attachment['file_size']
                        
                        category = attachment['category']
                        if category not in category_stats:
                            category_stats[category] = {'count': 0, 'size': 0}
                        
                        category_stats[category]['count'] += 1
                        category_stats[category]['size'] += attachment['file_size']
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'total_size_mb': round(total_size / 1024 / 1024, 2),
                'category_stats': category_stats
            }
            
        except Exception as e:
            logger.error(f"获取附件统计失败: {e}")
            return {
                'total_files': 0,
                'total_size': 0,
                'total_size_mb': 0,
                'category_stats': {}
            }